/**
 * Test Data Manager
 * Manages test data lifecycle - creation, cleanup, and seeding
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export class TestDataManager {
  private createdRecords: Map<string, string[]> = new Map()

  /**
   * Seed test database with initial data
   */
  async seedTestData(): Promise<void> {
    console.log('Seeding test data...')

    try {
      // Create test users
      await this.createTestUsers()

      // Create test couriers
      await this.createTestCouriers()

      // Create test vehicles
      await this.createTestVehicles()

      // Create test workflows
      await this.createTestWorkflows()

      console.log('Test data seeded successfully')
    } catch (error) {
      console.error('Error seeding test data:', error)
      throw error
    }
  }

  /**
   * Create test users
   */
  async createTestUsers(): Promise<void> {
    const users = [
      {
        email: 'admin@barq.com',
        password: 'admin123',
        name: 'Admin User',
        role: 'admin',
      },
      {
        email: 'manager@barq.com',
        password: 'manager123',
        name: 'Manager User',
        role: 'manager',
      },
      {
        email: 'hr@barq.com',
        password: 'hr123',
        name: 'HR User',
        role: 'hr',
      },
    ]

    const userIds: string[] = []

    for (const userData of users) {
      const user = await prisma.user.upsert({
        where: { email: userData.email },
        update: userData,
        create: userData,
      })
      userIds.push(user.id)
    }

    this.createdRecords.set('users', userIds)
  }

  /**
   * Create test couriers
   */
  async createTestCouriers(): Promise<void> {
    const couriers = [
      {
        name: 'Ahmed Hassan',
        email: 'ahmed.hassan@test.com',
        phone: '+966501234567',
        nationalId: '1234567890',
        nationality: 'Saudi',
        city: 'Riyadh',
        project: 'Jahez',
        status: 'active',
      },
      {
        name: 'Mohammed Ali',
        email: 'mohammed.ali@test.com',
        phone: '+966509876543',
        nationalId: '0987654321',
        nationality: 'Saudi',
        city: 'Jeddah',
        project: 'Hungerstation',
        status: 'active',
      },
      {
        name: 'Khalid Abdullah',
        email: 'khalid.abdullah@test.com',
        phone: '+966505555555',
        nationalId: '5555555555',
        nationality: 'Saudi',
        city: 'Riyadh',
        project: 'Jahez',
        status: 'inactive',
      },
    ]

    const courierIds: string[] = []

    for (const courierData of couriers) {
      const courier = await prisma.courier.create({
        data: courierData,
      })
      courierIds.push(courier.id)
    }

    this.createdRecords.set('couriers', courierIds)
  }

  /**
   * Create test vehicles
   */
  async createTestVehicles(): Promise<void> {
    const vehicles = [
      {
        plateNumber: 'ABC-1234',
        make: 'Toyota',
        model: 'Corolla',
        year: 2022,
        color: 'White',
        vin: 'JTDKB20U897654321',
        status: 'available',
      },
      {
        plateNumber: 'XYZ-5678',
        make: 'Honda',
        model: 'Civic',
        year: 2021,
        color: 'Silver',
        vin: 'JHMGE88507S111111',
        status: 'assigned',
      },
    ]

    const vehicleIds: string[] = []

    for (const vehicleData of vehicles) {
      const vehicle = await prisma.vehicle.create({
        data: vehicleData,
      })
      vehicleIds.push(vehicle.id)
    }

    this.createdRecords.set('vehicles', vehicleIds)
  }

  /**
   * Create test workflows
   */
  async createTestWorkflows(): Promise<void> {
    const courierIds = this.createdRecords.get('couriers') || []
    if (courierIds.length === 0) return

    const workflows = [
      {
        type: 'leave',
        title: 'Annual Leave Request',
        status: 'pending',
        courierId: courierIds[0],
        data: {
          startDate: '2025-02-01',
          endDate: '2025-02-05',
          reason: 'Family vacation',
        },
      },
      {
        type: 'loan',
        title: 'Emergency Loan',
        status: 'approved',
        courierId: courierIds[1],
        data: {
          amount: 5000,
          installments: 6,
          reason: 'Medical emergency',
        },
      },
    ]

    const workflowIds: string[] = []

    for (const workflowData of workflows) {
      const workflow = await prisma.workflowInstance.create({
        data: workflowData,
      })
      workflowIds.push(workflow.id)
    }

    this.createdRecords.set('workflows', workflowIds)
  }

  /**
   * Create test courier
   */
  async createTestCourier(data?: Partial<any>): Promise<any> {
    const courierData = {
      name: `Test Courier ${Date.now()}`,
      email: `test-${Date.now()}@example.com`,
      phone: `+96650${Math.floor(1000000 + Math.random() * 9000000)}`,
      nationalId: `${Math.floor(1000000000 + Math.random() * 9000000000)}`,
      nationality: 'Saudi',
      city: 'Riyadh',
      project: 'Jahez',
      status: 'active',
      ...data,
    }

    const courier = await prisma.courier.create({
      data: courierData,
    })

    const courierIds = this.createdRecords.get('couriers') || []
    courierIds.push(courier.id)
    this.createdRecords.set('couriers', courierIds)

    return courier
  }

  /**
   * Create test vehicle
   */
  async createTestVehicle(data?: Partial<any>): Promise<any> {
    const timestamp = Date.now()
    const vehicleData = {
      plateNumber: `TST-${timestamp}`,
      make: 'Toyota',
      model: 'Corolla',
      year: 2022,
      color: 'White',
      vin: `VIN${timestamp}`,
      status: 'available',
      ...data,
    }

    const vehicle = await prisma.vehicle.create({
      data: vehicleData,
    })

    const vehicleIds = this.createdRecords.get('vehicles') || []
    vehicleIds.push(vehicle.id)
    this.createdRecords.set('vehicles', vehicleIds)

    return vehicle
  }

  /**
   * Create test workflow
   */
  async createTestWorkflow(data?: Partial<any>): Promise<any> {
    const couriers = await prisma.courier.findMany({ take: 1 })
    if (couriers.length === 0) {
      throw new Error('No couriers available for workflow creation')
    }

    const workflowData = {
      type: 'leave',
      title: `Test Workflow ${Date.now()}`,
      status: 'pending',
      courierId: couriers[0].id,
      data: {
        startDate: '2025-02-01',
        endDate: '2025-02-05',
        reason: 'Test reason',
      },
      ...data,
    }

    const workflow = await prisma.workflowInstance.create({
      data: workflowData,
    })

    const workflowIds = this.createdRecords.get('workflows') || []
    workflowIds.push(workflow.id)
    this.createdRecords.set('workflows', workflowIds)

    return workflow
  }

  /**
   * Cleanup all created test data
   */
  async cleanupTestData(): Promise<void> {
    console.log('Cleaning up test data...')

    try {
      // Delete in reverse order of dependencies
      const workflowIds = this.createdRecords.get('workflows') || []
      if (workflowIds.length > 0) {
        await prisma.workflowInstance.deleteMany({
          where: { id: { in: workflowIds } },
        })
      }

      const vehicleIds = this.createdRecords.get('vehicles') || []
      if (vehicleIds.length > 0) {
        await prisma.vehicle.deleteMany({
          where: { id: { in: vehicleIds } },
        })
      }

      const courierIds = this.createdRecords.get('couriers') || []
      if (courierIds.length > 0) {
        await prisma.courier.deleteMany({
          where: { id: { in: courierIds } },
        })
      }

      // Don't delete users - they're reused across tests

      this.createdRecords.clear()
      console.log('Test data cleaned up successfully')
    } catch (error) {
      console.error('Error cleaning up test data:', error)
      throw error
    }
  }

  /**
   * Reset database to initial state
   */
  async resetDatabase(): Promise<void> {
    console.log('Resetting database...')

    try {
      // Delete all data in correct order
      await prisma.workflowInstance.deleteMany({})
      await prisma.vehicle.deleteMany({})
      await prisma.courier.deleteMany({})
      // Keep users for testing

      console.log('Database reset successfully')
    } catch (error) {
      console.error('Error resetting database:', error)
      throw error
    }
  }

  /**
   * Disconnect from database
   */
  async disconnect(): Promise<void> {
    await prisma.$disconnect()
  }
}

/**
 * Global test data manager instance
 */
export const testDataManager = new TestDataManager()

/**
 * Setup hook for tests
 */
export async function setupTestData(): Promise<void> {
  await testDataManager.seedTestData()
}

/**
 * Teardown hook for tests
 */
export async function teardownTestData(): Promise<void> {
  await testDataManager.cleanupTestData()
  await testDataManager.disconnect()
}
